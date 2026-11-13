#!/usr/bin/env python3
"""build_index.py: turns the QIA mirror's saved IBM calibration records into small static JSON for the /qia "Check a run" page.

Reads (never changes) ~/bones-forge/qia_mirror/records/<backend>/*.json(.gz) with the loader of qia_check.py itself, so a record is read
exactly as the QIA Research Package reads it, and the same rule drops a file that carries the same stamp as an earlier file (files sorted by
name, the first one wins). Nothing is precomputed. The page computes the four checks and the changes from the figures below.

Writes, under --out (default ./public/qia/records):
  index.json                      the processors, their first and newest stamp, and when this index was built
  <backend>/manifest.json         every record kept: stamp (UTC), file name, UTC day shard. Files dropped for a repeated stamp are listed.
  <backend>/<YYYY-MM-DD>.json     one UTC day of records. Per qubit, ten numbers: T1, its date, T2, its date, readout_error, its date,
                                  prob_meas1_prep0, its date, prob_meas0_prep1, its date. Dates are indexes into the shard's "dates" list,
                                  which holds IBM's own date strings. -1 = the figure has no date, -2 = the figure is not in the record.
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
def qrow(Q, i, dates, di):
    row = []
    for f in qc.FIELDS:
        v = Q.get(i, {}).get(f)
        if v is None: row += [None, -2]; continue
        d = v[1]
        if d is None: row += [v[0], -1]; continue
        d = str(d)
        if d not in di: di[d] = len(dates); dates.append(d)
        row += [v[0], di[d]]
    return row
def build_backend(rdir, out, days):
    name = os.path.basename(rdir); fs = sorted(glob.glob(os.path.join(rdir, '*.json')) + glob.glob(os.path.join(rdir, '*.json.gz')))
    recs, skipped, dup, seen = [], [], [], set()
    for p in fs:
        try: r = qc.load(p)
        except (ValueError, KeyError, json.JSONDecodeError, OSError): skipped.append(os.path.basename(p)); continue
        if (r[0], r[1]) in seen: dup.append(os.path.basename(p)); continue
        seen.add((r[0], r[1])); recs.append(r + (p,))
    recs.sort(key=lambda r: r[1])
    if not recs: return None
    if days: cut = recs[-1][1] - dt.timedelta(days=days); recs = [r for r in recs if r[1] >= cut]
    byday = {}
    for b, S, Q, p in recs: byday.setdefault(S.strftime('%Y-%m-%d'), []).append((b, S, Q, p))
    nq = max(len(r[2]) for r in recs); n = 0
    for day, rs in byday.items():
        dates, di, items = [], {}, []
        for b, S, Q, p in rs: items.append({'s': iso(S), 'f': os.path.basename(p), 'q': [qrow(Q, i, dates, di) for i in range(len(Q))]})
        n += write_if_changed(os.path.join(out, name, day + '.json'), dump({'dates': dates, 'records': items}))
    keep = set(byday)
    for old in glob.glob(os.path.join(out, name, '????-??-??.json')):
        if os.path.basename(old)[:-5] not in keep: os.remove(old); n += 1
    man = {'backend': name, 'fields': list(qc.FIELDS), 'qubits': nq, 'days_kept': days or None, 'built': iso(dt.datetime.now(UTC)),
           'records': [[iso(S), os.path.basename(p), S.strftime('%Y-%m-%d')] for b, S, Q, p in recs],
           'not_read_same_stamp': dup, 'not_records': skipped}
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
