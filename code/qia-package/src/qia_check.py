#!/usr/bin/env python3
"""qia_check.py -- QIA Research Package, Heuremen LLC (https://indahl.ai/qia). Standard library only.

Checks the IBM Quantum calibration record your run depends on, before the run and after it. Your files are opened read-only and are
never changed. Their sha256 is taken before and after and printed in the report. Reports go to a separate folder (default
./heuremen_report/). Run on saved files, it sends nothing anywhere. Only --pull contacts IBM, with your own saved account.
Python 3.9 or later. Times are UTC: give them with Z or an offset (2026-11-01T12:00:00Z).

  BEFORE A RUN   python qia_check.py before RECORD.json [--qubits 0,1,5]
  AFTER A RUN    python qia_check.py after RECORD_DIR --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z [--qubits 0,1,5]

RECORD.json is a backend's calibration record in Qiskit's BackendProperties format, saved with
  json.dump(backend.properties().to_dict(), open('record.json', 'w'), default=str)
(.json.gz also works). RECORD_DIR holds several such records from the same backend, for example one saved before and one after your run.
Optional: --pull BACKEND saves the current record with your own saved IBM account (pip install qiskit-ibm-runtime) and then checks it.

Before: for each qubit (all, or --qubits), the record's own figures are checked:
  STALE   T1 or T2 measured more than 24 hours before the record's last_update_date
  ZERO    an error value (readout_error, prob_meas1_prep0, prob_meas0_prep1) of exactly 0
  T2>2T1  a published pair with T2 above 2 x T1 (a single-exponential T2 cannot exceed 2 x T1). Above 2.5 x T1 reads ABOVE; between 2 and
          2.5 reads CANNOT_TELL. IBM publishes no fit width with the figures, so a band is needed, and we use 2.5 as its edge
  PAIR    T1 and T2 measured more than 24 hours apart
After: the latest record in the folder stamped at or before --start, every newer record stamped up to --end, and each change in the
T1, T2 and readout-error figures on your qubits from one record to the next. If IBM recalibrated between your last saved record and the
run, the record in force is not in the folder, so save one right before you submit. Compare your results against the record in force.

The checks read IBM's published figures only. They make no claim about your results. Free to run and cite with attribution; see LICENSE.txt."""
import json, gzip, sys, os, glob, hashlib, argparse, html, datetime as dt
UTC = dt.timezone.utc
ERRS = ('readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1'); FIELDS = ('T1', 'T2') + ERRS
NAME = 'QIA Research Package'; ORG = 'Heuremen LLC'; SITE = 'https://indahl.ai/qia'
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
def when(s):
    d = dt.datetime.fromisoformat(str(s).replace('Z', '+00:00')); return (d if d.tzinfo else d.replace(tzinfo=UTC)).astimezone(UTC)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def load(p):
    with (gzip.open(p, 'rt', encoding='utf-8') if p.endswith('.gz') else open(p, 'r', encoding='utf-8')) as f: d = json.load(f)
    if not isinstance(d, dict) or 'last_update_date' not in d or not isinstance(d.get('qubits'), list): raise ValueError('not a calibration record')
    Q = {}
    for i, qs in enumerate(d.get('qubits', [])):
        Q[i] = {x['name']: (x.get('value'), x.get('date'), x.get('unit', '')) for x in qs if x.get('name') in FIELDS}
    return d.get('backend_name', '?'), when(d['last_update_date']), Q
def check_record(S, Q, qubits):
    rows = []
    for q in qubits:
        e = Q.get(q, {}); t1, t2 = e.get('T1'), e.get('T2')
        for f in ('T1', 'T2'):
            if e.get(f) and e[f][1] and (S - when(e[f][1])).total_seconds() > 86400:
                rows.append(dict(qubit=q, check='STALE', field=f, detail=f'measured {when(e[f][1]):%Y-%m-%d %H:%M} UTC, {(S - when(e[f][1])).total_seconds() / 3600:.1f} h before the stamp'))
        for f in ERRS:
            if e.get(f) and e[f][0] == 0: rows.append(dict(qubit=q, check='ZERO', field=f, detail='published value exactly 0'))
        if t1 and t2 and t1[0] and t2[0] is not None and t1[0] > 0 and len(t1) > 2 and len(t2) > 2 and t1[2] != t2[2]:   # 1.0.1: units must match
            rows.append(dict(qubit=q, check='T2>2T1', field='T2/T1', detail=f'units differ ({t1[2]}, {t2[2]}), ratio not formed', outcome='CANNOT_TELL'))
        elif t1 and t2 and t1[0] and t2[0] is not None and t1[0] > 0:
            r = t2[0] / t1[0]
            if r > 2.0: rows.append(dict(qubit=q, check='T2>2T1', field='T2/T1', detail=f'ratio {r:.3f} (T1 {t1[0]:.4g}, T2 {t2[0]:.4g})', outcome='ABOVE' if r > 2.5 else 'CANNOT_TELL'))
            if t1[1] and t2[1]:
                gap = abs((when(t1[1]) - when(t2[1])).total_seconds()) / 3600
                if gap > 24: rows.append(dict(qubit=q, check='PAIR', field='T1/T2 dates', detail=f'{gap:.1f} h apart'))
    return rows
def page(title, meta, sections, inputs):
    css = ('body{font:16px/1.5 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:900px;margin:0 auto;padding:24px 16px}'
           'header{display:flex;gap:12px;align-items:center;border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:22px}'
           'table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #d8ccb4;padding:4px 6px;text-align:left}'
           '.note{color:#5a4d3a;font-size:14px}footer{margin-top:28px;border-top:1px solid #d8ccb4;padding-top:10px;font-size:13px;color:#5a4d3a}')
    h = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style><main>',
         f'<header>{LOGO}<div><b>{NAME}</b><br><span class="note">{ORG} &middot; <a href="{SITE}">{SITE}</a></span></div></header>', f'<h1>{html.escape(title)}</h1>']
    h += [f'<p class="note">{html.escape(m)}</p>' for m in meta]
    for st, rows, cols in sections:
        h.append(f'<h2>{html.escape(st)}</h2>')
        if not rows: h.append('<p>Nothing flagged.</p>'); continue
        h.append('<table><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cols) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{html.escape(str(r.get(c, "")))}</td>' for c in cols) + '</tr>' for r in rows) + '</table>')
    h.append('<footer>Your files were opened read-only and not changed. sha256 before and after:<br>' + '<br>'.join(f'{html.escape(os.path.basename(p))}: {a[:16]}&hellip; / {b[:16]}&hellip; {"unchanged" if a == b else "CHANGED"}' for p, a, b in inputs) +
             f'<br>These checks read IBM&rsquo;s published figures only and make no claim about your results. {ORG}, {SITE}</footer></main></html>')
    return '\n'.join(h)
def write(out, stem, title, meta, sections, inputs, data):
    os.makedirs(out, exist_ok=True); t = dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    hp, jp = os.path.join(out, f'{stem}_{t}.html'), os.path.join(out, f'{stem}_{t}.json')
    with open(hp, 'w', encoding='utf-8') as f: f.write(page(title, meta, sections, inputs))
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(dict(package=NAME, by=ORG, site=SITE, title=title, meta=meta, inputs=[dict(file=os.path.basename(p), sha256_before=a, sha256_after=b) for p, a, b in inputs], **data), f, indent=1, default=str)
    return hp, jp
def qlist(s, Q):
    if not s: return sorted(Q), []
    try: qs = [int(x) for x in s.split(',') if x.strip()]
    except ValueError: sys.exit('--qubits takes qubit numbers separated by commas, for example 0,1,5')
    return [q for q in qs if q in Q], [q for q in qs if q not in Q]
def utc(s, name):
    try: d = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError: sys.exit(f'{name}: give a UTC time like 2026-11-01T12:00:00Z')
    if d.tzinfo is None: sys.exit(f'{name}: add Z or an offset, so the time is not read in the wrong zone')
    return d.astimezone(UTC)
def fmt(v): return '' if v is None else (f'{v:.4g}' if isinstance(v, (int, float)) else str(v))
def pull(backend, dest):
    from qiskit_ibm_runtime import QiskitRuntimeService   # your own saved account
    b = QiskitRuntimeService().backend(backend); p = os.path.join(dest, f'{backend}_{dt.datetime.now(UTC):%Y%m%dT%H%M%SZ}.json')
    os.makedirs(dest, exist_ok=True); json.dump(b.properties().to_dict(), open(p, 'w'), default=str); return p
def main():
    ap = argparse.ArgumentParser(description=NAME + ', ' + ORG); sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('before'); a1.add_argument('record', nargs='?'); a1.add_argument('--qubits'); a1.add_argument('--pull'); a1.add_argument('--out', default='heuremen_report')
    a2 = sub.add_parser('after'); a2.add_argument('records'); a2.add_argument('--start', required=True); a2.add_argument('--end', required=True); a2.add_argument('--qubits'); a2.add_argument('--out', default='heuremen_report'); a2.add_argument('--backend', help='which backend to read when the folder holds records from several')
    a = ap.parse_args()
    if a.cmd == 'before':
        if a.record and a.pull: sys.exit('give RECORD.json or --pull BACKEND, not both')
        rec = a.record or (pull(a.pull, os.path.join(a.out, 'records')) if a.pull else sys.exit('give RECORD.json or --pull BACKEND'))
        h0 = sha(rec)
        try: b, S, Q = load(rec)
        except (ValueError, KeyError, json.JSONDecodeError): sys.exit(rec + ' is not a calibration record (Qiskit BackendProperties JSON)')
        qs, miss = qlist(a.qubits, Q); rows = check_record(S, Q, qs); h1 = sha(rec)
        age = (dt.datetime.now(UTC) - S).total_seconds() / 3600
        meta = [f'Backend {b}, record stamped {S:%Y-%m-%d %H:%M} UTC, {age:.1f} h before this check. Qubits checked: {len(qs)}.',
                'IBM recalibrates during the day. Save the record again right before you submit, and keep it with your data.'] + ([f'Not in this record, so not checked: qubits {", ".join(map(str, miss))}.'] if miss else [])
        cols = ['qubit', 'check', 'field', 'detail', 'outcome']
        hp, jp = write(a.out, f'before_{b}', f'Before the run: {b}', meta, [(f'Flags ({len(rows)})', rows, cols)], [(rec, h0, h1)], dict(backend=b, stamp=S.isoformat(), qubits=qs, flags=rows))
    else:
        rd = os.path.realpath(a.records); od = os.path.realpath(a.out)
        if od == rd or od.startswith(rd + os.sep): sys.exit('--out must be outside the records folder')
        st = utc(a.start, '--start'); en = utc(a.end, '--end')
        if en < st: sys.exit('--end is earlier than --start')
        fs = sorted(glob.glob(os.path.join(a.records, '*.json')) + glob.glob(os.path.join(a.records, '*.json.gz')))
        if not fs: sys.exit('no records in ' + a.records)
        hs = {p: sha(p) for p in fs}; recs, skipped, seen = [], [], set()
        for p in fs:
            try: r = load(p)
            except (ValueError, KeyError, json.JSONDecodeError, OSError): skipped.append(os.path.basename(p)); continue
            if (r[0], r[1]) in seen: skipped.append(os.path.basename(p) + ' (same stamp as another file)'); continue
            seen.add((r[0], r[1])); recs.append(r + (p,))
        recs.sort(key=lambda r: r[1])
        bk = sorted({r[0] for r in recs})   # 1.0.1 (13 Nov 2026): records from different backends are never diffed against each other
        if a.backend:
            other = [x for x in bk if x != a.backend]; recs = [r for r in recs if r[0] == a.backend]
            if not recs: sys.exit(f'no records from {a.backend} in {a.records} (backends found: {", ".join(bk)})')
        elif len(bk) > 1: sys.exit(f'{a.records} holds records from several backends ({", ".join(bk)}); give --backend NAME')
        else: other = []
        under = [r for r in recs if r[1] <= st]; during = [r for r in recs if st < r[1] <= en]
        meta = [f'Run window {st:%Y-%m-%d %H:%M} to {en:%Y-%m-%d %H:%M} UTC. Records read: {len(recs)}.'] + ([f'Records from other backends were ignored: {", ".join(other)}.'] if other else []) + ([f'Not read as records: {", ".join(skipped)}.'] if skipped else [])
        secs = []; data = {}
        if not under: meta.append('No record in the folder is stamped at or before the run start, so the record in force at the start is not here. Save the record right before you submit.')
        else:
            b, S, Q, p = under[-1]; qs, miss = qlist(a.qubits, Q)
            meta.append(f'The latest record in this folder stamped at or before the start: {S:%Y-%m-%d %H:%M} UTC ({os.path.basename(p)}). If IBM recalibrated after it and before the run, the record in force is not in the folder.')
            if miss: meta.append(f'Not in this record, so not checked: qubits {", ".join(map(str, miss))}.')
            secs.append(('Flags in that record', check_record(S, Q, qs), ['qubit', 'check', 'field', 'detail', 'outcome']))
            ch = []; prev = (S, Q)
            for b2, S2, Q2, p2 in during:
                for q in qs:
                    for f in FIELDS:
                        v1, v2 = prev[1].get(q, {}).get(f), Q2.get(q, {}).get(f)
                        if (v1 or v2) and (v1 or (None, None))[:2] != (v2 or (None, None))[:2]:
                            ch.append(dict(record=f'{S2:%Y-%m-%d %H:%M}', qubit=q, field=f, before=fmt(v1 and v1[0]), after=fmt(v2 and v2[0]), date_before=(v1 or ('', ''))[1], date_after=(v2 or ('', ''))[1]))
                prev = (S2, Q2)
            meta.append(f'Records stamped during the run: {len(during)}.' + (' T1, T2 or readout-error figures on your qubits changed during the run; see the table.' if ch else ''))
            secs.append(('T1, T2 and readout-error figures that changed during the run (each record against the one before it)', ch, ['record', 'qubit', 'field', 'before', 'after', 'date_before', 'date_after']))
            data = dict(backend=b, record_at_start=S.isoformat(), records_during=[r[1].isoformat() for r in during], changes=ch, skipped=skipped)
        hp, jp = write(a.out, 'after', 'After the run: the record at the start, and what changed', meta, secs, [(p, hs[p], sha(p)) for p in fs], data)
    print(NAME, '|', ORG, '|', SITE); print('report:', hp); print('data:  ', jp)
if __name__ == '__main__': main()
