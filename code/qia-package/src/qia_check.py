#!/usr/bin/env python3
"""qia_check.py -- QIA Research Package, Heuremen LLC (https://indahl.ai/qia). Standard library only. Version 1.0.3.

Checks the IBM Quantum calibration record your run depends on, before the run and after it. Your files are opened read-only and are
never changed. Their sha256 is taken before and after and printed in the report. Reports go to a separate folder (default
./heuremen_report/). Run on saved files, it sends nothing anywhere. Only --pull contacts IBM, with your own saved account.
Python 3.9 or later. Give times in UTC with Z or an offset (2026-11-01T12:00:00Z).

  BEFORE A RUN   python qia_check.py before RECORD.json [--at RUN_TIME] [--qubits 0,1,5]
  AFTER A RUN    python qia_check.py after RECORD_DIR --start 2026-11-01T12:00:00Z --end 2026-11-01T12:40:00Z [--qubits 0,1,5]

RECORD.json is a backend's calibration record in Qiskit's BackendProperties format, saved with
  json.dump(backend.properties().to_dict(), open('record.json', 'w'), default=str)
(.json.gz also works). RECORD_DIR holds several such records from the same backend, for example one saved before and one after your run.
Optional: --pull BACKEND saves the current record with your own saved IBM account (pip install qiskit-ibm-runtime) and then checks it.

Before: for each qubit (all, or --qubits), the record's own figures are checked:
  STALE    any figure read (T1, T2, readout_error, prob_meas1_prep0, prob_meas0_prep1, init_error) measured more than 24 hours before the
           record's stamp, or more than 24 hours before the run (--at; default: the time of this check). Both ages are printed.
  ZERO     an error value (readout_error, prob_meas1_prep0, prob_meas0_prep1) equal to 0 (also "0" and -0.0). A 0 read from 1024 shots
           still allows a true error up to 0.29 % (95 %, one-sided); a value such as 1e-17 cannot come from any shot count.
  T2>2T1   a published pair with T2 above 2 x T1 (a single-exponential T2 cannot exceed 2 x T1). Above 2.5 x T1 reads ABOVE; between 2 and
           2.5 reads CANNOT_TELL. IBM publishes no fit width with the figures, so a band is needed, and we use 2.5 as its edge
  PAIR     T1 and T2 measured more than 24 hours apart (read even when a T1 or T2 value itself is unusable)
  UNKNOWN  a figure that cannot be read: absent, null, NaN, zero or negative T1/T2, an unknown unit, an unparseable date, conflicting
           duplicate entries, a date with no zone, or a qubit with no figures. UNKNOWN is never a pass.
After: the latest record of the same backend stamped at or before --start, every newer record of that backend stamped up to --end, the
same checks on each of them, and each change in the figures on your qubits from one record to the next. A folder that mixes backends is refused
unless --backend names one. Two files with the same stamp and different contents are both checked and reported as a conflict.
Gates and zz are NOT read by this package. Every flag and change carries a category: T1 and T2, or Error figures.

The checks read IBM's published figures only. They make no claim about your results. Free to run and cite with attribution; see LICENSE."""
import json, gzip, sys, os, glob, hashlib, argparse, html, math, re, datetime as dt
VERSION = '1.0.3'
UTC = dt.timezone.utc
ERRS = ('readout_error', 'prob_meas1_prep0', 'prob_meas0_prep1'); TIMES = ('T1', 'T2'); FIELDS = TIMES + ERRS + ('init_error',)
UNIT_US = {'': 1.0, 'us': 1.0, 'µs': 1.0, 'μs': 1.0, 'ns': 1e-3, 'ms': 1e3, 's': 1e6}   # T1/T2 normalised to microseconds (R12)
NAME = 'QIA Research Package'; ORG = 'Heuremen LLC'; SITE = 'https://indahl.ai/qia'
LOGO = ('<svg viewBox="0 0 200 200" width="44" height="44" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="9">'
        '<polygon points="100,30 180,170 20,170"/><polygon points="100,170 139,84 61,84"/><circle cx="100" cy="112" r="5" fill="currentColor"/></svg>')
DAY = 86400.0; TOL = 1e-9

def when(s):
    """-> (UTC datetime, naive?) ; raises ValueError on an unparseable date. Leap second :60 is read as :59 + 1 s (R07)."""
    t = str(s).strip().replace('Z', '+00:00'); leap = False
    m = re.match(r'^(.*T\d\d:\d\d:)60(\.\d+)?(.*)$', t)
    if m: t = m.group(1) + '59' + (m.group(2) or '') + m.group(3); leap = True
    try: d = dt.datetime.fromisoformat(t); naive = d.tzinfo is None
    except OverflowError: raise ValueError('date out of range: %r' % (s,))
    try: d = (d.replace(tzinfo=UTC) if naive else d).astimezone(UTC)
    except OverflowError: raise ValueError('date out of range: %r' % (s,))
    try: return (d + dt.timedelta(seconds=1) if leap else d), naive
    except OverflowError: raise ValueError('date out of range: %r' % (s,))

def num(v):
    """-> float or None. Numeric strings are read (R09); NaN and non-numbers are None."""
    if isinstance(v, bool) or v is None: return None
    try: x = float(v)
    except (TypeError, ValueError, OverflowError): return None
    return None if math.isnan(x) or math.isinf(x) else x

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def load(p):
    try:
        with (gzip.open(p, 'rt', encoding='utf-8') if p.endswith('.gz') else open(p, 'r', encoding='utf-8')) as f: d = json.load(f)
    except RecursionError: raise ValueError('nested too deeply to read')
    if not isinstance(d, dict) or 'last_update_date' not in d or not isinstance(d.get('qubits'), list): raise ValueError('not a calibration record')
    try: S, naive = when(d['last_update_date'])
    except (ValueError, TypeError): raise ValueError('record stamp unreadable: %r' % (d['last_update_date'],))
    if naive: raise ValueError('record stamp %r has no zone, so every age measured from it would be a guess; refused' % (d['last_update_date'],))
    Q = {}
    for i, qs in enumerate(d.get('qubits', [])):
        e = {}
        for x in (qs if isinstance(qs, list) else []):
            if isinstance(x, dict) and x.get('name') in FIELDS: e.setdefault(x['name'], []).append((x.get('value'), x.get('date'), (x['unit'] if isinstance(x.get('unit'), str) else (None if x.get('unit') is None else '?' + type(x.get('unit')).__name__))))
        Q[i] = e   # every entry kept, so duplicates can be seen (R11)
    return d.get('backend_name', '?'), S, Q

def check_record(S, Q, qubits, ref=None, ref_name='the run'):
    rows = []; U = lambda q, f, why: rows.append(dict(qubit=q, check='UNKNOWN', field=f, detail=why, outcome='UNKNOWN'))
    for q in qubits:
        e = Q.get(q, {})
        if not e: U(q, '(all)', 'no figures: no T1, T2 or error figure for this qubit in the record'); continue
        val, date = {}, {}
        for f in TIMES:
            if f not in e: U(q, f, 'absent from the record')   # P04: a missing T1/T2 is never a pass
        for f, entries in e.items():
            if len(set((repr(num(v) if num(v) is not None else v), str(t), str(u or '')) for v, t, u in entries)) > 1:   # conflicting duplicates (R11)
                U(q, f, f'{len(entries)} conflicting entries in one record; none used'); continue
            v, t, u = entries[0]
            if t not in (None, ''):
                try:
                    d, naive = when(t)
                    if naive: U(q, f, f'date {t} has no zone, so its age cannot be known; not read')
                    else: date[f] = d
                except (ValueError, TypeError): U(q, f, f'date {t!r} cannot be read')
            else: U(q, f, 'no measurement date, so its age cannot be checked')
            x = num(v)
            if f in TIMES:
                if u is None: U(q, f, 'no unit given'); continue
                if u not in UNIT_US: U(q, f, f'unknown unit {u!r}'); continue
                if x is None or x <= 0: U(q, f, f'value {v!r} is not a usable time'); continue
                val[f] = x * UNIT_US[u]
            else:
                if u not in ('', None, '%'): U(q, f, f'unknown unit {u!r} for an error rate'); continue
                if x is None: U(q, f, f'value {v!r} cannot be read'); continue
                if u == '%': x = x / 100
                if x < 0: U(q, f, f'value {v!r} is negative, not a usable error rate'); continue
                val[f] = x
        for f, d in date.items():   # every field read is aged (R01), against the stamp and against the run (R02)
            a_s = (S - d).total_seconds(); a_r = (ref - d).total_seconds() if ref else None
            if a_s > DAY or (a_r is not None and a_r > DAY):
                rows.append(dict(qubit=q, check='STALE', field=f, detail=f'measured {d:%Y-%m-%d %H:%M} UTC: {a_s / 3600:.1f} h before the stamp' +
                                 (f', {a_r / 3600:.1f} h before {ref_name}' if a_r is not None else '')))
        for f in ERRS + ('init_error',):
            if f in val and val[f] == 0: rows.append(dict(qubit=q, check='ZERO', field=f, detail='published value 0'))
            elif f in val and 0 < abs(val[f]) < 1e-6: rows.append(dict(qubit=q, check='TINY', field=f, detail=f'published value {val[f]!r}: below 1e-6, which no count of up to 1,000,000 shots can give'))
        for f, d in date.items():
            if (d - S).total_seconds() > 0: rows.append(dict(qubit=q, check='FUTURE', field=f, detail=f'measured {d:%Y-%m-%d %H:%M} UTC, {(d - S).total_seconds() / 3600:.1f} h AFTER the record stamp'))
        if 'T1' in val and 'T2' in val:
            r = val['T2'] / val['T1']
            if r > 2.0 * (1 + TOL):   # float edge (R10)
                rows.append(dict(qubit=q, check='T2>2T1', field='T2/T1', detail=f'ratio {r:.3f} (T1 {val["T1"]:.4g} us, T2 {val["T2"]:.4g} us)',
                                 outcome='ABOVE' if r > 2.5 * (1 + TOL) else 'CANNOT_TELL'))
        if 'T1' in date and 'T2' in date:   # PAIR no longer hides behind the T1 value (R03)
            gap = abs((date['T1'] - date['T2']).total_seconds()) / 3600
            if gap > 24: rows.append(dict(qubit=q, check='PAIR', field='T1/T2 dates', detail=f'{gap:.1f} h apart'))
    rows.sort(key=lambda r: (r['check'] == 'UNKNOWN',))   # real flags above UNKNOWN rows (stable)
    for r in rows:   # 13 Nov 2026: two categories, T1 and T2 against the error figures
        f = str(r.get('field', ''))
        r['category'] = 'T1 and T2' if (r['check'] in ('T2>2T1', 'PAIR') or f in ('T1', 'T2')) else 'Error figures'
    return rows

def page(title, meta, sections, inputs, empty=None):
    css = ('body{font:16px/1.5 Georgia,serif;background:#f6efe2;color:#1c1712;margin:0}main{max-width:900px;margin:0 auto;padding:24px 16px}'
           'header{display:flex;gap:12px;align-items:center;border-bottom:2px solid #c9a227;padding-bottom:12px}header b{font-size:22px}'
           'table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #d8ccb4;padding:4px 6px;text-align:left}'
           '.note{color:#5a4d3a;font-size:14px}footer{margin-top:28px;border-top:1px solid #d8ccb4;padding-top:10px;font-size:13px;color:#5a4d3a}')
    h = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style><main>',
         f'<header>{LOGO}<div><b>{NAME}</b> {VERSION}<br><span class="note">{ORG} &middot; <a href="{SITE}">{SITE}</a></span></div></header>', f'<h1>{html.escape(title)}</h1>']
    h += [f'<p class="note">{html.escape(m)}</p>' for m in meta]
    for st, rows, cols in sections:
        h.append(f'<h2>{html.escape(st)}</h2>')
        if not rows: h.append('<p>' + html.escape((empty or {}).get(st, 'Nothing flagged in the fields this package reads (gates and zz are not read).')) + '</p>'); continue
        h.append('<table><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cols) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{html.escape(str(r.get(c, "")))}</td>' for c in cols) + '</tr>' for r in rows) + '</table>')
    h.append('<footer>Your files were opened read-only and not changed. sha256 before and after:<br>' + '<br>'.join(f'{html.escape(os.path.basename(p))}: {a[:16]}&hellip; / {b[:16]}&hellip; {"unchanged" if a == b else "CHANGED"}' for p, a, b in inputs) +
             f'<br>These checks read IBM&rsquo;s published figures only and make no claim about your results. Gates and zz are not read. {ORG}, {SITE}</footer></main></html>')
    return '\n'.join(h)

def safe(name): return re.sub(r'[^A-Za-z0-9._-]', '_', str(name).encode('utf-8', 'replace').decode('utf-8'))[:80] or 'record'
def write(out, stem, title, meta, sections, inputs, data):
    stem = safe(stem)
    try: os.makedirs(out, exist_ok=True)
    except OSError as ex: sys.exit(f'--out {out}: cannot write a report there ({type(ex).__name__})')
    if not os.path.isdir(out): sys.exit(f'--out {out}: not a folder')
    t = dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'); ec = data.pop('_empty_changes', None); ef = data.pop('_empty_flags', None); efb = data.pop('_empty_flags_before', None)
    hp, jp = os.path.join(out, f'{stem}_{t}.html'), os.path.join(out, f'{stem}_{t}.json')
    with open(hp, 'w', encoding='utf-8', errors='replace') as f: f.write(page(title, meta, sections, inputs, {'Figures that changed during the run (each record against the one before it)': ec or 'No figure changed between records in the run window (in the fields read).', 'Flags in the record at the start and in records stamped during the run': ef or 'Nothing flagged in the fields this package reads (gates and zz are not read).', **({f'Flags (0)': efb} if efb else {})}))
    with open(jp, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(dict(package=NAME, version=VERSION, by=ORG, site=SITE, title=title, meta=meta,
                       inputs=[dict(file=os.path.basename(p), sha256_before=a, sha256_after=b) for p, a, b in inputs], **data), f, indent=1, default=str)
    return hp, jp

def qlist(s, Q):
    if not s: return sorted(Q), []
    try: qs = [int(x) for x in s.split(',') if x.strip()]
    except ValueError: sys.exit('--qubits takes qubit numbers separated by commas, for example 0,1,5')
    return [q for q in qs if q in Q], [q for q in qs if q not in Q]

def utc(s, name):
    try: d = dt.datetime.fromisoformat(s.replace('Z', '+00:00')); d.astimezone(UTC)
    except (ValueError, OverflowError): sys.exit(f'{name}: give a UTC time like 2026-11-01T12:00:00Z')
    if d.tzinfo is None: sys.exit(f'{name}: add Z or an offset, so the time is not read in the wrong zone')
    return d.astimezone(UTC)

def fmt(v):
    if v is None: return ''
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        try: return f'{v:.4g}'
        except (OverflowError, ValueError): t = str(v); return t[:12] + '...' + t[-4:] if len(t) > 20 else t
    return str(v)
def first(e, f): x = e.get(f); return x[0] if x else None

def pull(backend, dest):
    from qiskit_ibm_runtime import QiskitRuntimeService   # your own saved account
    b = QiskitRuntimeService().backend(backend); p = os.path.join(dest, f'{backend}_{dt.datetime.now(UTC):%Y%m%dT%H%M%SZ}.json')
    os.makedirs(dest, exist_ok=True); json.dump(b.properties().to_dict(), open(p, 'w'), default=str); return p

COLS = ['category', 'qubit', 'check', 'field', 'detail', 'outcome']
def figs(Qx):   # a record's figures, independent of file bytes and key order: two records conflict only if these differ
    return json.dumps({str(q): {f: [[num(x[0]) if num(x[0]) is not None else x[0], x[1], x[2] or ''] for x in e[f]] for f in sorted(e)} for q, e in sorted(Qx.items())}, sort_keys=True, default=str)
UNK_TEXT = 'UNKNOWN row(s) (a figure, entry or qubit that could not be read: absent, unusable, zoneless or conflicting. An (all) row is one qubit with no figures)'   # 13 Nov, Sage: counts are rows, not figures
def main():
    ap = argparse.ArgumentParser(description=f'{NAME} {VERSION}, {ORG}'); sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('before'); a1.add_argument('record', nargs='?'); a1.add_argument('--qubits'); a1.add_argument('--pull'); a1.add_argument('--out', default='heuremen_report')
    a1.add_argument('--at', help='the run time (UTC); figures older than 24 h at this time are STALE. Default: now')
    a2 = sub.add_parser('after'); a2.add_argument('records'); a2.add_argument('--start', required=True); a2.add_argument('--end', required=True); a2.add_argument('--qubits'); a2.add_argument('--out', default='heuremen_report'); a2.add_argument('--backend', help='use only records of this backend')
    a = ap.parse_args()
    if a.cmd == 'before':
        if a.record and a.pull: print(f'note: --pull {a.pull} ignored because RECORD.json was given', file=sys.stderr)
        rec = a.record or (pull(a.pull, os.path.join(a.out, 'records')) if a.pull else sys.exit('give RECORD.json or --pull BACKEND'))
        try: os.path.realpath(a.out)
        except (OSError, ValueError) as ex: sys.exit(f'--out {a.out}: not a usable folder ({type(ex).__name__})')
        if a.record and not os.path.isfile(a.record): sys.exit(f'{a.record}: not a readable file')
        if a.record:
            rd0 = os.path.dirname(os.path.realpath(rec)); od0 = os.path.realpath(a.out)
            if od0 == os.path.realpath(os.path.dirname(os.path.abspath(rec))): sys.exit('--out must not be the folder that holds the record (a report there could later be read as a record)')
            if od0 == rd0: sys.exit('--out must not be the folder that holds the record (a report there could later be read as a record)')
        try: h0 = sha(rec); b, S, Q = load(rec)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, OSError, UnicodeDecodeError, OverflowError, EOFError) as ex: sys.exit(f'{rec} is not a readable calibration record (Qiskit BackendProperties JSON): {ex}')
        at = utc(a.at, '--at') if a.at else dt.datetime.now(UTC)
        qs, miss = qlist(a.qubits, Q); rows = check_record(S, Q, qs, at, 'the run time' if a.at else 'this check'); h1 = sha(rec)
        unk = sum(r['check'] == 'UNKNOWN' for r in rows)
        meta = [(f'{len(rows) - unk} flag row(s), {unk} ' + UNK_TEXT + '.') if qs else 'NO QUBIT WAS CHECKED: this page is not a pass.', f'Backend {b}, record stamped {S:%Y-%m-%d %H:%M} UTC, {(at - S).total_seconds() / 3600:.1f} h before {"the run time " + format(at, "%Y-%m-%d %H:%M") + " UTC" if a.at else "this check"}. Qubits checked: {len(qs)}.',
                'IBM recalibrates during the day. Save the record again right before you submit, and keep it with your data.', 'Gates and zz are not read by this package.']
        if not qs: meta.append('NO QUBITS CHECKED: the record has no qubits, or none of the ones asked for. Nothing here is a pass.')
        if unk: meta.append(f'{unk} UNKNOWN row(s): something could not be read. UNKNOWN is not a pass.')
        if miss: meta.append(f'Not in this record, so not checked: qubits {", ".join(map(str, miss))}.')
        # 13 Nov 2026, Sage: before reads one file. Look for other files in the same folder with the same stamp and say what was not checked.
        sib = []
        if a.record:
            for p2 in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(rec)), '*.json')) + glob.glob(os.path.join(os.path.dirname(os.path.abspath(rec)), '*.json.gz'))):
                if os.path.realpath(p2) == os.path.realpath(rec): continue
                try: b2, S2, Q2 = load(p2)
                except Exception: continue
                if b2 == b and S2 == S: sib.append((os.path.basename(p2), figs(Q2) != figs(Q)))
        if sib:
            nd = [n for n, d in sib if d]
            meta.append(f'{len(sib)} other file(s) in this folder carry the same stamp' + (f', {len(nd)} with different figures ({", ".join(nd)})' if nd else ', with the same figures') + '. before checks only the file given. Run after over the folder to check every one.')
        else: meta.append('before reads only this file. Other records with the same stamp, if any exist outside this folder, were not seen.')
        tt = [r for r in rows if r.get('category') == 'T1 and T2']; ee = [r for r in rows if r.get('category') != 'T1 and T2']
        hp, jp = write(a.out, f'before_{b}', f'Before the run: {b}', meta, [(f'T1 and T2 flags ({len(tt)})', tt, COLS), (f'Error-figure flags ({len(ee)})', ee, COLS)], [(rec, h0, h1)],
                       dict(_empty_flags_before=None if qs else 'Nothing was checked: no qubit to read.', backend=b, stamp=S.isoformat(), run_time=at.isoformat(), qubits=qs, flags=rows, unknown=unk))
    else:
        try: rd = os.path.realpath(a.records); od = os.path.realpath(a.out)
        except (OSError, ValueError) as ex: sys.exit(f'--out or the records folder is not a usable path ({type(ex).__name__})')
        if od == rd: sys.exit('--out must not be the records folder (a report there would be read as a record)')
        st = utc(a.start, '--start'); en = utc(a.end, '--end')
        if en < st: sys.exit('--end is earlier than --start')
        fs = sorted(glob.glob(os.path.join(a.records, '*.json')) + glob.glob(os.path.join(a.records, '*.json.gz')))
        if not fs: sys.exit('no records in ' + a.records)
        hs = {}; recs, skipped, conflicts = [], [], []
        for p in fs:
            try:
                if not os.path.isfile(p): raise ValueError('not a file')
                hs[p] = sha(p); r = load(p); recs.append((str(r[0]),) + r[1:] + (p,))
            except (ValueError, KeyError, TypeError, json.JSONDecodeError, OSError, UnicodeDecodeError, OverflowError, EOFError) as ex: skipped.append(f'{os.path.basename(p)} ({type(ex).__name__}: {str(ex)[:80]})')
        fs = [p for p in fs if p in hs]
        recs.sort(key=lambda r: (r[1], r[3]))
        meta = [f'Run window {st:%Y-%m-%d %H:%M} to {en:%Y-%m-%d %H:%M} UTC. Records read: {len(recs)}.', 'Gates and zz are not read by this package.']
        secs = []; data = dict(flags=[], skipped=skipped)
        names = sorted(set(r[0] for r in recs))
        if a.backend: b = a.backend
        elif len(names) > 1: sys.exit(f'the folder mixes backends ({", ".join(names)}); give --backend NAME; refused')
        elif names: b = names[0]
        else: sys.exit('no readable records in ' + a.records + (': ' + '; '.join(skipped) if skipped else ''))
        for r in recs:
            if r[0] != b: skipped.append(f'{os.path.basename(r[3])} (backend {r[0]}, not {b})')
        recs = [r for r in recs if r[0] == b]   # one backend per run; other backends are never mixed in (R13, H1)
        for x, y in zip(recs, recs[1:]):   # same stamp, different contents: report and check both (R15)
            if x[1] == y[1] and figs(x[2]) != figs(y[2]): conflicts.append(f'{os.path.basename(x[3])} and {os.path.basename(y[3])} share the stamp {x[1]:%Y-%m-%d %H:%M} UTC and differ')
        under = [r for r in recs if r[1] <= st]; during = [r for r in recs if st < r[1] <= en]
        in_force = [r for r in under if r[1] == under[-1][1]] if under else []
        allq = set().union(*[set(r[2]) for r in recs]) if recs else set()
        qs, miss = qlist(a.qubits, {q: 1 for q in allq})
        meta.append(f'Backend {b}.')
        if in_force: meta.append(f'The latest record stamped at or before the start: {in_force[0][1]:%Y-%m-%d %H:%M} UTC ({", ".join(os.path.basename(r[3]) for r in in_force)}). If IBM recalibrated after it and before the run, the record in force is not in the folder.')
        else: meta.append('NO RECORD in the folder is stamped at or before the run start, so the record in force at the start is not here. Records stamped during the run are still checked below. Save the record right before you submit.')
        meta.append(f'Records stamped during the run: {len(during)}' + (f' ({", ".join(os.path.basename(r[3]) for r in during)}).' if during else '.'))
        if conflicts: meta.append('CONFLICT: ' + '; '.join(conflicts) + '. Both are checked below.')
        if skipped: meta.append(f'Not used: {", ".join(skipped)}.')
        if miss: meta.append(f'Not in these records, so not checked: qubits {", ".join(map(str, miss))}.')
        flags = []
        for _, S1, Q1, p1 in (in_force if len(set(figs(r[2]) for r in in_force)) > 1 else in_force[:1]):
            fr = check_record(S1, Q1, qs, st, 'the run start'); [r.update(record=os.path.basename(p1)) for r in fr]; flags += fr
        for _, S2, Q2, p2 in during:   # records stamped during the run get the same checks (R14, H1)
            fr = check_record(S2, Q2, qs, en, 'the run end'); [r.update(record=os.path.basename(p2)) for r in fr]; flags += fr
        flags.sort(key=lambda r: (r['check'] == 'UNKNOWN',)); nu = sum(r['check'] == 'UNKNOWN' for r in flags)
        nchk = (len(in_force[:1]) + len(during)) if qs else 0
        if nu and nchk: meta.insert(0, f'{nu} figure(s) could not be read (UNKNOWN). UNKNOWN is not a pass.')
        meta.insert(0, (f'{len(flags) - nu} flag row(s), {nu} ' + UNK_TEXT + '.') if nchk else ('NO QUBIT WAS CHECKED: none of the asked qubits is in these records. This page is not a pass.' if (in_force or during) else 'NO RECORD WAS CHECKED: no record of this backend is stamped at or before the start or during the run. This page is not a pass.'))
        secs.append(('Flags in the record at the start and in records stamped during the run', flags, ['record'] + COLS))
        empty_flags = None if nchk else ('Nothing was checked: no qubit to read.' if (in_force or during) else 'Nothing was checked: there is no record to read.')
        ch = []
        for (_, Sa, Qa, pa), (_, Sb, Qb, pb_) in zip(in_force, in_force[1:]):   # CONFLICT: same-stamp records compared to each other
            for q in qs:
                for f in FIELDS:
                    v1, v2 = first(Qa.get(q, {}), f), first(Qb.get(q, {}), f)
                    fk = lambda v: None if not v else (num(v[0]) if num(v[0]) is not None else repr(v[0]), str(v[1]), str(v[2] or ''))
                    if (v1 or v2) and fk(v1) != fk(v2):
                        ch.append(dict(record=f'CONFLICT {os.path.basename(pa)} vs {os.path.basename(pb_)}', qubit=q, field=f, before=fmt(v1 and v1[0]) + (f' {v1[2]}' if v1 and v1[2] else ''), after=fmt(v2 and v2[0]) + (f' {v2[2]}' if v2 and v2[2] else ''), date_before=(v1 or ('', ''))[1], date_after=(v2 or ('', ''))[1]))
        def diff(Qa, Qb, label):
            for q in qs:
                for f in FIELDS:
                    v1, v2 = first(Qa.get(q, {}), f), first(Qb.get(q, {}), f)
                    key = lambda v: None if not v else (num(v[0]) if num(v[0]) is not None else repr(v[0]), str(v[1]), str(v[2] or ''))
                    if not (v1 or v2) or key(v1) == key(v2): continue
                    known = bool(v1 and v2) and f in TIMES and (v1[2] or '') in UNIT_US and (v2[2] or '') in UNIT_US and num(v1[0]) is not None and num(v2[0]) is not None
                    unit_only = known and str(v1[1]) == str(v2[1]) and (v1[2] or '') != (v2[2] or '') and math.isclose(num(v1[0]) * UNIT_US[v1[2] or ''], num(v2[0]) * UNIT_US[v2[2] or ''], rel_tol=1e-9)
                    ch.append(dict(record=label + (' (unit only, same value)' if unit_only else ''), qubit=q, field=f,
                                   before=fmt(v1 and v1[0]) + (f' {v1[2]}' if v1 and v1[2] else ''), after=fmt(v2 and v2[0]) + (f' {v2[2]}' if v2 and v2[2] else ''),
                                   date_before=(v1 or ('', ''))[1], date_after=(v2 or ('', ''))[1]))
        conflict_at_start = len(in_force) > 1 and len(set(figs(r[2]) for r in in_force)) > 1
        bases = in_force if conflict_at_start else in_force[:1]   # agreeing same-stamp records count once (no doubled rows)
        if during:
            for br in bases:   # the FIRST during-run record against each base; labelled only when there is a conflict
                diff(br[2], during[0][2], f'{during[0][1]:%Y-%m-%d %H:%M}' + (f' (from {os.path.basename(br[3])})' if conflict_at_start else ''))
            for (_, S1, Q1, p1), (_, S2, Q2, p2) in zip(during, during[1:]):   # later records against the one before them, once
                diff(Q1, Q2, f'{S2:%Y-%m-%d %H:%M} (from {os.path.basename(p1)})')
        if ch: meta.append('Figures on your qubits changed during the run; see the table.')
        for c in ch: c['category'] = 'T1 and T2' if c.get('field') in ('T1', 'T2') else 'Error figures'
        secs.append(('Figures that changed during the run (each record against the one before it)', ch, ['record', 'category', 'qubit', 'field', 'before', 'after', 'date_before', 'date_after']))
        nrec = len(in_force) + len(during)   # CONFLICT: two same-stamp records at the start both count
        data = dict(_empty_flags=empty_flags, _empty_changes='No figure changed between records in the run window (in the fields read).' if nrec >= 2 else 'Nothing to compare: fewer than two records (the record at the start and any stamped during the run).', backend=b, record_at_start=in_force[0][1].isoformat() if in_force else None, records_during=[r[1].isoformat() for r in during], flags=flags, changes=ch, conflicts=conflicts, skipped=skipped)
        hp, jp = write(a.out, 'after', 'After the run: the record at the start, and what changed', meta, secs, [(p, hs[p], sha(p)) for p in fs], data)
    print(NAME, VERSION, '|', ORG, '|', SITE); print('report:', hp); print('data:  ', jp)
    if not qs or (a.cmd == 'after' and not data.get('backend')) or (a.cmd == 'after' and not (data.get('record_at_start') or data.get('records_during'))): print('NOTHING WAS CHECKED: this report is not a pass (exit 2)', file=sys.stderr); sys.exit(2)
if __name__ == '__main__': main()
