#!/usr/bin/env python3
"""Compares qia_check.py (the QIA Research Package) with runcheck.js (run in node) on the same records.
Snapshots the mirror's records, builds the index from the snapshot, runs both on fixed run windows plus whole-history sweeps, and compares exactly.
Usage: python3 -I tests/run_compare.py   (writes tests/last_result.json)"""
import sys, os, json, glob, shutil, subprocess, tempfile, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); ROOT = os.path.expanduser('~/bones-forge')
sys.path.insert(0, os.path.join(ROOT, 'qia_package', 'src')); import qia_check as qc
MIRROR = os.path.join(ROOT, 'qia_mirror', 'records'); CHECK = os.path.join(ROOT, 'qia_package', 'src', 'qia_check.py')
CASES = [
 dict(name='fez, records stamped during the run', backend='ibm_fez', start='2026-10-30 11:00', end='2026-10-30 12:30', qubits='0,1,5,70,155'),
 dict(name='marrakesh, several records during the run, one qubit not on the chip', backend='ibm_marrakesh', start='2026-10-30 21:55', end='2026-10-30 23:10', qubits='0,1,5,70,155,200'),
 dict(name='kingston, no record during the run', backend='ibm_kingston', start='2026-10-30 14:00', end='2026-10-30 14:30', qubits='0,1,2,3,100'),
 dict(name='boston, twelve hours, every qubit', backend='ibm_boston', start='2026-10-31 06:00', end='2026-10-31 18:00', qubits=''),
 dict(name='phoenix, a qubit not on the chip', backend='ibm_phoenix', start='2026-10-30 08:00', end='2026-10-30 20:00', qubits='0-9,119,120'),
 dict(name='pittsburgh, run across midnight UTC, every qubit', backend='ibm_pittsburgh', start='2026-10-30 22:00', end='2026-10-31 03:00', qubits=''),
 dict(name='aachen, run before the first saved record', backend='ibm_aachen', start='2026-10-20 08:00', end='2026-10-20 09:00', qubits='0,1'),
]
def py_case(c, recdir):
    tmp = tempfile.mkdtemp(); z = lambda x: x.replace(' ', 'T') + (':00' if len(x) == 16 else '') + 'Z'; st = z(c['start']); en = z(c['end'])
    qa = ['--qubits', c['qubits'].replace('-', ',') if '-' not in c['qubits'] else ','.join(str(i) for p in c['qubits'].split(',') for i in (range(int(p.split('-')[0]), int(p.split('-')[1]) + 1) if '-' in p else [int(p)]))] if c['qubits'] else []
    r = subprocess.run([sys.executable, '-I', CHECK, 'after', recdir, '--start', st, '--end', en, '--out', tmp] + qa, capture_output=True, text=True)
    if r.returncode: return dict(file=None, stamp=None, during=[], flags=[], changes=[], missing=[], note=r.stdout + r.stderr)
    j = json.load(open(glob.glob(os.path.join(tmp, 'after_*.json'))[0]))
    if 'record_at_start' not in j: return dict(file=None, stamp=None, during=[], flags=[], changes=[], missing=[])
    S = qc.when(j['record_at_start']); fs = sorted(glob.glob(os.path.join(recdir, '*.json')) + glob.glob(os.path.join(recdir, '*.json.gz')))
    f = next(p for p in fs if qc.load(p)[1] == S)   # the first file with that stamp, as the package reads them
    b = subprocess.run([sys.executable, '-I', CHECK, 'before', f, '--out', tmp] + qa, capture_output=True, text=True, check=True)
    bj = json.load(open(glob.glob(os.path.join(tmp, 'before_*.json'))[0]))
    shutil.rmtree(tmp)
    iso = lambda d: qc.when(d).strftime('%Y-%m-%dT%H:%M:%SZ')
    _, _, Q = qc.load(f); want = [int(x) for x in qa[1].split(',')] if qa else []
    return dict(file=os.path.basename(f), stamp=iso(j['record_at_start']), during=[iso(x) for x in j['records_during']],
                flags=[{k: v for k, v in x.items()} for x in bj['flags']], changes=j['changes'], missing=[q for q in want if q not in Q])
def main():
    work = tempfile.mkdtemp(); snap = os.path.join(work, 'records'); idx = os.path.join(work, 'index')
    shutil.copytree(MIRROR, snap)
    subprocess.run([sys.executable, '-I', os.path.join(BASE, 'build_index.py'), '--records', snap, '--out', idx, '--days', '0'], check=True, capture_output=True)
    cases = [dict(c) for c in CASES]; backends = sorted(os.listdir(snap))
    cases += [dict(name='sweep ' + b, backend=b, sweep=True) for b in backends]
    cj = os.path.join(work, 'cases.json'); json.dump(cases, open(cj, 'w'))
    js = json.loads(subprocess.run(['node', os.path.join(HERE, 'js_driver.js'), idx, cj], check=True, capture_output=True, text=True).stdout)
    res = []; ok = True
    for c in CASES:
        p = py_case(c, os.path.join(snap, c['backend'])); j = js[c['name']]
        same = all(p[k] == j[k] for k in ('file', 'stamp', 'during', 'flags', 'changes', 'missing'))
        ok &= same
        res.append(dict(case=c['name'], backend=c['backend'], start=c['start'], end=c['end'], qubits=c['qubits'] or 'all', record_in_force=p['stamp'], records_during=len(p['during']), flags=len(p['flags']), changes=len(p['changes']),
                        missing=p['missing'], identical=same))
        if not same:
            for k in ('file', 'stamp', 'during', 'flags', 'changes', 'missing'):
                if p[k] != j[k]: print('DIFF', c['name'], k, str(p[k])[:300], '|||', str(j[k])[:300])
    # sweeps: every record, every qubit, check_record of the package against the page code; and whole-history changes via the package CLI
    for b in backends:
        fs = sorted(glob.glob(os.path.join(snap, b, '*.json')) + glob.glob(os.path.join(snap, b, '*.json.gz'))); seen = set(); nrec = nflag = 0; same = True
        for p in fs:
            r = qc.load(p)
            if (r[0], r[1]) in seen: continue
            seen.add((r[0], r[1])); S = r[1]; key = S.strftime('%Y-%m-%dT%H:%M:%SZ'); mine = qc.check_record(S, r[2], sorted(r[2])); theirs = js['sweep ' + b]['flags'].get(key)
            nrec += 1; nflag += len(mine)
            if mine != theirs: same = False; print('SWEEP DIFF', b, key)
        first = min(r[1] for r in (qc.load(p) for p in fs)); whole = dict(name='whole', backend=b, start=first.strftime('%Y-%m-%d %H:%M:%S'), end='2026-12-01 00:00', qubits='')
        pw = py_case(whole, os.path.join(snap, b)); cj2 = os.path.join(work, 'c2.json'); json.dump([whole], open(cj2, 'w'))
        jw = json.loads(subprocess.run(['node', os.path.join(HERE, 'js_driver.js'), idx, cj2], check=True, capture_output=True, text=True).stdout)['whole']
        csame = all(pw[k] == jw[k] for k in ('file', 'stamp', 'during', 'flags', 'changes'))
        ok &= same and csame
        res.append(dict(case='whole history ' + b, backend=b, records=nrec, flag_rows_all_records=nflag, flags_identical=same, records_during=len(pw['during']), changes=len(pw['changes']), changes_identical=csame))
    json.dump(res, open(os.path.join(HERE, 'last_result.json'), 'w'), indent=1)
    for r in res: print(json.dumps(r))
    print('ALL IDENTICAL' if ok else 'MISMATCH'); shutil.rmtree(work); sys.exit(0 if ok else 1)
main()
