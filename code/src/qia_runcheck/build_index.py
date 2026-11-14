#!/usr/bin/env python3
"""build_index.py: turns the QIA mirror's saved IBM calibration records into small static JSON for the /qia "Check a run" page.

Reads (never changes) ~/bones-forge/qia_mirror/records/<backend>/*.json(.gz) with the loader of qia_check.py itself, so a record is read
exactly as the QIA Research Package reads it. Files that carry the same stamp are all kept, sorted by stamp and then file name, as the
package orders them, so the page can show a repeated stamp and compare the files as the package does. Nothing is precomputed. The page computes the checks and the changes from the figures below, with the rules of qia_check.py.

Writes, under --out (default ./public/qia/records):
  index.json                      the processors, their first and newest stamp, and when this index was built
  <backend>/manifest.json         every record kept: stamp (UTC), file name, UTC day shard. Unreadable files are listed under not_records.
  <backend>/<YYYY-MM-DD>.json     one UTC day of records: {"dates": [...], "units": [...], "orders": [...], "records": [{"s","f","q"}, ...]}.
    FIELDS are the six qia_check.FIELDS: 0 T1, 1 T2, 2 readout_error, 3 prob_meas1_prep0, 4 prob_meas0_prep1, 5 init_error.
    "dates" holds IBM's own date strings, "units" the unit strings, "orders" strings of field digits such as "012345".
    A qubit is one list: [o, v, d, u, v, d, u, ...(, extras)]. o indexes "orders": the fields present for that qubit, in the order they
    first appear in the record (qia_check keeps that order, and its rows follow it). After o come three numbers per listed field, in that
    order: v the value, d an index into "dates" (-1 = no date), u an index into "units" (-1 = no unit key). A field absent from the qubit is
    simply not listed. If a field has more than one entry in the record, the first sits in its slot and the others come last as extras,
    a list of [field digit, v, d, u] (qia_check keeps duplicates and calls conflicting ones UNKNOWN, so the page must see them).
    A value v is plain JSON when it is null, true/false, a string, an integer below 2^53, or a non-integral finite float. Anything else
    (an integral float such as 0.0, NaN, infinity, a huge integer, a list or object) is {"r": Python repr, "t": "f"|"i"|"o"}, so the page
    can tell 0 from 0.0 and print the value as Python does. Nothing is precomputed.
Only the last --days days (default 30, counted back from the newest record of each processor) are kept. Older shards are removed.
A file is rewritten only when its content changed, so a refresh after one new record touches one shard and one manifest.
Usage: python3 -I build_index.py [--records DIR] [--out DIR] [--days 30] [--backend NAME]"""
import sys, os, glob, json, argparse, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.expanduser('~/bones-forge')
sys.path.insert(0, os.path.join(ROOT, 'qia_package', 'src'))
import qia_check as qc
UTC = dt.timezone.utc
def iso(d): return d.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def dump(o): return json.dumps(o, separators=(',', ':'), ensure_ascii=False)
def write_if_changed(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, encoding='utf-8').read() == text: return 0
    tmp = path + '.tmp'; open(tmp, 'w', encoding='utf-8').write(text); os.replace(tmp, path); return 1
# 13 Nov: the page applies the rules of qia_check.check_record, so shards carry every field it reads (qc.FIELDS), with unit and duplicates.
FIELDS = tuple(qc.FIELDS)
def val(v):
    if v is None or isinstance(v, (bool, str)): return v
    if type(v) is int: return v if abs(v) < 2 ** 53 else {'r': repr(v), 't': 'i'}
    if type(v) is float: return v if (v == v and abs(v) != float('inf') and not v.is_integer()) else {'r': repr(v), 't': 'f'}
    return {'r': repr(v), 't': 'o'}
def idx(x, lst, di):
    if x is None: return -1
    x = str(x)
    if x not in di: di[x] = len(lst); lst.append(x)
    return di[x]
def qrow(Q, i, S):
    dates, di, units, ui, orders, oi = S
    e = Q.get(i, {}); order = ''.join(str(FIELDS.index(f)) for f in e)
    if order not in oi: oi[order] = len(orders); orders.append(order)
    row = [oi[order]]; extra = []
    for f, es in e.items():
        for k, (v, d, u) in enumerate(es):
            c = [val(v), idx(d, dates, di), idx(u, units, ui)]
            if k == 0: row += c
            else: extra.append([FIELDS.index(f)] + c)
    if extra: row.append(extra)
    return row
def build_backend(rdir, out, days):
    name = os.path.basename(rdir); fs = sorted(glob.glob(os.path.join(rdir, '*.json')) + glob.glob(os.path.join(rdir, '*.json.gz')))
    recs, skipped = [], []
    for p in fs:
        try: r = qc.load(p)
        except (ValueError, KeyError, json.JSONDecodeError, OSError): skipped.append(os.path.basename(p)); continue
        recs.append(r + (p,))
    recs.sort(key=lambda r: (r[1], r[3]))
    if not recs: return None
    if days: cut = recs[-1][1] - dt.timedelta(days=days); recs = [r for r in recs if r[1] >= cut]
    byday = {}
    for b, S, Q, p in recs: byday.setdefault(S.strftime('%Y-%m-%d'), []).append((b, S, Q, p))
    nq = max(len(r[2]) for r in recs); n = 0
    for day, rs in byday.items():
        sh = ([], {}, [], {}, [], {}); items = []
        for b, S, Q, p in rs: items.append({'s': iso(S), 'f': os.path.basename(p), 'q': [qrow(Q, i, sh) for i in range(len(Q))]})
        n += write_if_changed(os.path.join(out, name, day + '.json'), dump({'dates': sh[0], 'units': sh[2], 'orders': sh[4], 'records': items}))
    keep = set(byday)
    for old in glob.glob(os.path.join(out, name, '????-??-??.json')):
        if os.path.basename(old)[:-5] not in keep: os.remove(old); n += 1
    man = {'backend': name, 'format': 2, 'fields': list(FIELDS), 'qubits': nq, 'days_kept': days or None, 'built': iso(dt.datetime.now(UTC)),
           'records': [[iso(S), os.path.basename(p), S.strftime('%Y-%m-%d')] for b, S, Q, p in recs],
           'not_records': skipped}
    # "built" changes on every run, so keep the old one when nothing else did
    mp = os.path.join(out, name, 'manifest.json')
    if os.path.exists(mp):
        try:
            old = json.load(open(mp, encoding='utf-8')); o2 = dict(old); m2 = dict(man); o2.pop('built', None); m2.pop('built', None)
            if o2 == m2: man['built'] = old['built']
        except (ValueError, KeyError): pass
    n += write_if_changed(mp, dump(man))
    return {'backend': name, 'first': man['records'][0][0], 'newest': man['records'][-1][0], 'records': len(recs), 'days': len(byday), 'files_written': n}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--records', default=os.path.join(ROOT, 'qia_mirror', 'records'))
    ap.add_argument('--out', default=os.path.join(HERE, 'public', 'qia', 'records')); ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--backend'); a = ap.parse_args()
    dirs = sorted(d for d in glob.glob(os.path.join(a.records, 'ibm_*')) if os.path.isdir(d) and (not a.backend or os.path.basename(d) == a.backend))
    info = [x for x in (build_backend(d, a.out, a.days) for d in dirs) if x]
    ip = os.path.join(a.out, 'index.json')
    if a.backend and os.path.exists(ip):   # a one-processor refresh keeps the others' rows
        keep = [x for x in json.load(open(ip, encoding='utf-8')).get('processors', []) if x['backend'] != a.backend]; info = sorted(keep + info, key=lambda x: x['backend'])
    idx = {'processors': [{k: x[k] for k in ('backend', 'first', 'newest', 'records', 'days')} for x in info], 'built': iso(dt.datetime.now(UTC))}
    idx['updated'] = max((x['newest'] for x in idx['processors']), default=None)   # 2 Nov: the newest record stamp, read by the watch for staleness
    if os.path.exists(ip):
        try:
            o = json.load(open(ip, encoding='utf-8'))
            if o.get('processors') == idx['processors']: idx['built'] = o['built']
        except ValueError: pass
    write_if_changed(ip, dump(idx))
    for x in info: print(f"{x['backend']}: {x['records']} records, {x['days']} days, {x['files_written']} files written")
if __name__ == '__main__': main()
