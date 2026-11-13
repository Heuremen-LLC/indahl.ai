"""Referee second pass: content types (incl. CONTENT_TYPE_AD), incompatible_content_illegal and decision visibility for the mapped platforms.
Groups by platform, application-date period (H2/H1/other), created-date period, automated_decision, source_type, decision_ground,
incompatible_content_illegal, content-type mask. Output: out/ct.parquet"""
import sys, os, site, glob
sys.path.append(site.getusersitepackages())
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount_db import MAPPED, day_str

CT = ['CONTENT_TYPE_APP', 'CONTENT_TYPE_AUDIO', 'CONTENT_TYPE_IMAGE', 'CONTENT_TYPE_PRODUCT', 'CONTENT_TYPE_SYNTHETIC_MEDIA', 'CONTENT_TYPE_TEXT',
      'CONTENT_TYPE_VIDEO', 'CONTENT_TYPE_OTHER', 'CONTENT_TYPE_LINK', 'CONTENT_TYPE_ACCOUNT', 'CONTENT_TYPE_AD', 'CONTENT_TYPE_STICKER', 'CONTENT_TYPE_HASHTAG']
COLS = ['platform_name', 'automated_decision', 'source_type', 'decision_ground', 'incompatible_content_illegal', 'application_date', 'created_at', 'count'] + CT

def per_of(d):
    # d: date32 array -> 'H2' / 'H1' / 'X'
    s = pc.cast(d, pa.string())
    h2 = pc.and_(pc.greater_equal(s, '2025-07-01'), pc.less_equal(s, '2025-12-31'))
    h1 = pc.and_(pc.greater_equal(s, '2026-01-01'), pc.less_equal(s, '2026-06-30'))
    return pc.if_else(pc.fill_null(h2, False), 'H2', pc.if_else(pc.fill_null(h1, False), 'H1', 'X'))

def one(mdir):
    parts = []
    for f in sorted(glob.glob(os.path.join(mdir, '**', 'part-*.parquet'), recursive=True)):
        t = pq.read_table(f, columns=COLS)
        t = t.filter(pc.is_in(t['platform_name'], value_set=pa.array(MAPPED)))
        if t.num_rows == 0: continue
        mask = None
        for c in CT:
            v = pc.if_else(t[c], c.replace('CONTENT_TYPE_', '')[:3], '')
            mask = v if mask is None else pc.binary_join_element_wise(mask, v, '.')
        tt = pa.table({'platform': t['platform_name'], 'papp': per_of(day_str(t['application_date'])), 'pcre': per_of(day_str(t['created_at'])),
                       'ad': t['automated_decision'], 'src': t['source_type'], 'gr': t['decision_ground'], 'icil': t['incompatible_content_illegal'],
                       'ct': mask, 'isad': t['CONTENT_TYPE_AD'], 'n': t['count']})
        parts.append(tt.group_by(['platform', 'papp', 'pcre', 'ad', 'src', 'gr', 'icil', 'ct', 'isad']).aggregate([('n', 'sum')]))
    if not parts: return None
    return pa.concat_tables(parts).group_by(['platform', 'papp', 'pcre', 'ad', 'src', 'gr', 'icil', 'ct', 'isad']).aggregate([('n_sum', 'sum')]).rename_columns(['platform', 'papp', 'pcre', 'ad', 'src', 'gr', 'icil', 'ct', 'isad', 'n'])

if __name__ == '__main__':
    unz, out = sys.argv[1], sys.argv[2]
    mdirs = sorted(glob.glob(os.path.join(unz, 'aggregated-complete-*')))
    res = []
    with ProcessPoolExecutor(max_workers=9) as ex:
        for m, r in zip(mdirs, ex.map(one, mdirs)):
            if r is not None: res.append(r.append_column('month', pa.array([os.path.basename(m)] * r.num_rows)))
            print('done', m, flush=True)
    pq.write_table(pa.concat_tables(res), os.path.join(out, 'ct.parquet'))
    print('ALL DONE')
