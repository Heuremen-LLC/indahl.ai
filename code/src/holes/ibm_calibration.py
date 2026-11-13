#!/usr/bin/env python3
"""OUTSIDE HOLES #2 -- IBM Quantum backend calibration history, 2026-09-26.

Read-only: backend.properties(datetime=...) is a plain REST GET of IBM's own calibration record
(/api/v1/backends/<name>/properties?updated_before=...). No jobs, no sessions, no runtime seconds.

For every backend the key can see, one snapshot per UTC day (as of 23:59:59) from the earliest day IBM still
serves up to yesterday (complete UTC days). Raw snapshots cached (gzipped) under cache/ibm/<backend>/<YYYY-MM-DD>.json.gz (404 days cached as {}).
Distinct calibrations are de-duplicated by last_update_date, then holes are written, runs merged across snapshots:
  kind 'qubit-nonoperational'  IBM's own operational flag = 0 on a qubit
  kind 'gate-nonoperational'   IBM's operational flag = 0 on a gate, or gate_error >= 1 (IBM's "broken" marker)
  kind 'qubit-extreme'         T1 < 10 us, readout_error >= 0.25, or T1/readout missing/NaN
  kind 'no-calibration'        > 36 h between consecutive distinct calibrations, or a day IBM returns 404 inside coverage
  at = calibration timestamp where the condition first appears, ended = first calibration where it is gone ('' = still open).
Appends to outside_holes.jsonl (provider 'ibm-calibration', dedup by id).

Usage: ~/bones-forge/qvenv/bin/python ibm_calibration.py      (re-run any time; complete UTC days only, cached days are not refetched)
"""
import gzip, json, math, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache', 'ibm')
OUT = os.path.join(HERE, 'outside_holes.jsonl')
LOOKBACK_DAYS = 900
T1_MIN_US, RO_MAX, GAP_H = 10.0, 0.25, 36

from qiskit_ibm_runtime import QiskitRuntimeService
svc = QiskitRuntimeService(channel='ibm_quantum_platform', instance='open-instance',
                           token=open(os.path.expanduser('~/bones-forge/.ibm_quantum_key')).read().strip())


def snap(backend, day):
    d = os.path.join(CACHE, backend.name); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, f'{day}.json.gz')
    if os.path.exists(fn):
        return json.load(gzip.open(fn, 'rt'))
    t = dt.datetime.fromisoformat(day).replace(hour=23, minute=59, second=59, tzinfo=dt.timezone.utc)
    try:
        p = backend.properties(datetime=t)
        raw = p.to_dict() if p else {}
    except Exception as e:
        if '404' not in str(e): raise
        raw = {}
    with gzip.open(fn, 'wt') as f: json.dump(raw, f, default=str)
    return json.loads(json.dumps(raw, default=str))


def pmap(params):
    return {x['name']: x.get('value') for x in params}


def bad_float(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


def conditions(raw):
    """-> {(kind, target): reason} for one calibration snapshot."""
    out = {}
    for qi, params in enumerate(raw.get('qubits', [])):
        m = pmap(params)
        if 'operational' in m and not m['operational']:
            out[('qubit-nonoperational', f'q{qi}')] = 'IBM operational flag = 0'
        t1, ro = m.get('T1'), m.get('readout_error')
        why = []
        if bad_float(t1): why.append('T1 missing/NaN')
        elif t1 < T1_MIN_US: why.append(f'T1 < {T1_MIN_US:g} us')
        if bad_float(ro): why.append('readout_error missing/NaN')
        elif ro >= RO_MAX: why.append(f'readout_error >= {RO_MAX}')
        if why: out[('qubit-extreme', f'q{qi}')] = '; '.join(why)
    for g in raw.get('gates', []):
        m = pmap(g.get('parameters', []))
        tgt = g.get('name') or f"{g.get('gate')}{'_'.join(map(str, g.get('qubits', [])))}"
        if 'operational' in m and not m['operational']:
            out[('gate-nonoperational', tgt)] = 'IBM operational flag = 0'
        elif not bad_float(m.get('gate_error')) and m['gate_error'] >= 1:
            out[('gate-nonoperational', tgt)] = 'gate_error >= 1'
    return out


def walk(backend):
    today = dt.datetime.now(dt.timezone.utc).date()
    days = [(today - dt.timedelta(days=k)).isoformat() for k in range(LOOKBACK_DAYS, 0, -1)]   # complete UTC days only (today is still moving)
    snaps = [(d, snap(backend, d)) for d in days]
    first = next((i for i, (_, r) in enumerate(snaps) if r), None)
    if first is None: return [], None
    snaps = snaps[first:]
    holes, runs, prev_cal, prev_raw = [], {}, None, None
    distinct, missing_days = [], []
    for d, raw in snaps:
        if not raw: missing_days.append(d); continue
        if raw['last_update_date'] == prev_cal: continue
        distinct.append((d, raw)); prev_cal = raw['last_update_date']
    name = backend.name
    for d in missing_days:
        holes.append({'id': f'ibm-cal:{name}:404:{d}', 'provider': 'ibm-calibration', 'device': name, 'status': 'NO_PROPERTIES',
                      'at': f'{d}T00:00:00Z', 'ended': f'{d}T23:59:59Z', 'shots': None,
                      'reason': 'IBM returned 404 for properties as of this day inside the covered range', 'kind': 'no-calibration'})
    for (d0, r0), (d1, r1) in zip(distinct, distinct[1:]):
        a, b = dt.datetime.fromisoformat(r0['last_update_date']), dt.datetime.fromisoformat(r1['last_update_date'])
        if (b - a) > dt.timedelta(hours=GAP_H):
            holes.append({'id': f'ibm-cal:{name}:gap:{r0["last_update_date"]}', 'provider': 'ibm-calibration', 'device': name,
                          'status': 'NO_CALIBRATION', 'at': r0['last_update_date'], 'ended': r1['last_update_date'],
                          'shots': None, 'reason': f'{(b - a).total_seconds() / 3600:.1f} h between consecutive calibrations',
                          'kind': 'no-calibration'})
    for d, raw in distinct:
        cal = raw['last_update_date']
        cur = conditions(raw)
        for key in list(runs):
            if key not in cur:
                h = runs.pop(key); h['ended'] = cal; holes.append(h)
        for key, why in cur.items():
            if key not in runs:
                kind, tgt = key
                runs[key] = {'id': f'ibm-cal:{name}:{kind}:{tgt}:{cal}', 'provider': 'ibm-calibration', 'device': f'{name}/{tgt}',
                             'status': kind.upper(), 'at': cal, 'ended': '', 'shots': None, 'reason': why, 'kind': kind}
    holes += runs.values()                            # still open at the latest calibration
    return holes, (distinct[0][1]['last_update_date'], distinct[-1][1]['last_update_date'], len(distinct), len(missing_days))


def main():
    seen = {json.loads(l)['id'] for l in open(OUT) if l.strip()} if os.path.exists(OUT) else set()
    backends = svc.backends()
    with ThreadPoolExecutor(len(backends)) as pool:
        results = list(pool.map(walk, backends))
    allh = []
    for b, (holes, cov) in zip(backends, results):
        kinds = {}
        for h in holes: kinds[h['kind']] = kinds.get(h['kind'], 0) + 1
        print(f'{b.name}: coverage {cov[0] if cov else None} .. {cov[1] if cov else None}, {cov[2] if cov else 0} distinct calibrations, '
              f'{cov[3] if cov else 0} 404-days; holes {len(holes)} {kinds}')
        allh += holes
    # an open run whose id already exists is kept as-is; a run that has since closed gets a new line with 'ended' filled
    new = [h for h in allh if h['id'] not in seen]
    closed_ids = {h['id'] for h in allh if h['ended']}
    reclosed = [h for h in allh if h['id'] in seen and h['ended'] and h['id'] in closed_ids]
    if os.path.exists(OUT) and reclosed:
        lines = [json.loads(l) for l in open(OUT) if l.strip()]
        upd = {h['id']: h for h in reclosed}
        lines = [upd.get(x['id'], x) if not x.get('ended') else x for x in lines]
        with open(OUT, 'w') as f:
            for x in lines: f.write(json.dumps(x) + '\n')
    with open(OUT, 'a') as f:
        for h in new: f.write(json.dumps(h) + '\n')
    print(f'ibm-calibration holes: {len(allh)} total; {len(new)} new appended')


if __name__ == '__main__':
    main()
