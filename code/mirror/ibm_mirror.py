#!/usr/bin/env python3
"""ibm_mirror.py: mirrors the calibration IBM publishes for every processor we can see. Runs on the HST tick bus, never on a timer.
Per run, per processor: read the published properties (no QPU seconds used), save the full record whenever IBM's stamp or values change,
append one row per read to polls.jsonl (COMMITTED / NOTHING_RETURNED), and rewrite summary.json for the QIA page. Keys are read from the
key files and passed straight to the service, never printed or stored."""
import os, sys, json, gzip, hashlib, time, statistics as S, datetime as D
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.expanduser('~/bones-forge')
sys.path.insert(0, os.path.join(ROOT, 'qvenv', 'lib'))
def svc():
    from qiskit_ibm_runtime import QiskitRuntimeService
    last = 'no key'
    for kf in ('.ibm_quantum_key', '.ibm_quantum_key_2', '.ibm_quantum_key_3'):
        try: return QiskitRuntimeService(channel='ibm_quantum_platform', token=open(os.path.join(ROOT, kf)).read().strip())
        except Exception as e: last = type(e).__name__
    raise RuntimeError(last)
def med(x): x = [v for v in x if v is not None]; return round(S.median(x), 6) if x else None
def stats(p):
    q = p.get('qubits', []); T1 = []; T2 = []; RO = []
    for qq in q:
        d = {x['name']: x['value'] for x in qq}; T1.append(d.get('T1')); T2.append(d.get('T2')); RO.append(d.get('readout_error'))
    g2 = []
    for g in p.get('gates', []):
        if len(g.get('qubits', [])) == 2:
            for x in g.get('parameters', []):
                if x['name'] == 'gate_error': g2.append(x['value'])
    return dict(n_qubits=len(q), t1_us=med(T1), t2_us=med(T2), readout_error=med(RO), two_qubit_error=med(g2))
def main():
    state_f = os.path.join(HERE, 'state.json'); state = json.load(open(state_f)) if os.path.exists(state_f) else {}
    now = time.time(); polls = open(os.path.join(HERE, 'polls.jsonl'), 'a'); changes = open(os.path.join(HERE, 'changes.jsonl'), 'a')
    try: service = svc(); names = sorted(b.name for b in service.backends(simulator=False, operational=True))
    except Exception as e:
        polls.write(json.dumps(dict(at=now, status='NOTHING_RETURNED', why=type(e).__name__)) + '\n'); print('mirror: no service', type(e).__name__); return
    for n in names:
        try:
            p = service.backend(n).properties(refresh=True).to_dict()
        except Exception as e:
            polls.write(json.dumps(dict(at=now, backend=n, status='NOTHING_RETURNED', why=type(e).__name__)) + '\n'); continue
        stamp = str(p.get('last_update_date')); body = json.dumps({k: p[k] for k in ('qubits', 'gates') if k in p}, sort_keys=True, default=str)
        h = hashlib.sha256((stamp + body).encode()).hexdigest()[:16]; vh = hashlib.sha256(body.encode()).hexdigest()[:16]; st = state.get(n, {}); changed = st.get('hash') != h; vchanged = st.get('vh') != vh
        polls.write(json.dumps(dict(at=now, backend=n, status='COMMITTED', stamp=stamp, hash=h, changed=changed)) + '\n')
        if changed:
            sd = os.path.join(HERE, 'records', n); os.makedirs(sd, exist_ok=True)
            fn = os.path.join(sd, stamp.replace(':', '-').replace('+', 'p').replace(' ', 'T') + '.json.gz')
            with gzip.open(fn, 'wt') as f: f.write(json.dumps(p, default=str))
            s = stats(p); changes.write(json.dumps(dict(at=now, backend=n, stamp=stamp, hash=h, values_changed=vchanged, **s)) + '\n'); st = dict(hash=h, vh=vh, stamp=stamp, **s)
        st['last_read'] = now; state[n] = st
    json.dump(state, open(state_f, 'w'), indent=1); polls.close(); changes.close()
    wk = now - 7 * 86400; ch = [json.loads(l) for l in open(os.path.join(HERE, 'changes.jsonl'))]; pl = [json.loads(l) for l in open(os.path.join(HERE, 'polls.jsonl'))]
    out = []
    for n in sorted(state):
        s = state[n]; out.append(dict(backend=n, stamp=s['stamp'], n_qubits=s['n_qubits'], t1_us=s['t1_us'], t2_us=s['t2_us'], readout_error=s['readout_error'], two_qubit_error=s['two_qubit_error'],
            records_saved=sum(1 for c in ch if c['backend'] == n), restamps_7d=sum(1 for c in ch if c['backend'] == n and c['at'] >= wk), value_changes_7d=sum(1 for c in ch if c['backend'] == n and c['at'] >= wk and c.get('values_changed')), reads=sum(1 for q in pl if q.get('backend') == n and q['status'] == 'COMMITTED'),
            missed=sum(1 for q in pl if q.get('backend') == n and q['status'] != 'COMMITTED'), last_read=D.datetime.utcfromtimestamp(s['last_read']).strftime('%d %b %H:%M'), since=D.datetime.utcfromtimestamp(min(c['at'] for c in ch if c['backend'] == n)).strftime('%d %b %Y')))
    json.dump(dict(updated=D.datetime.utcfromtimestamp(now).strftime('%d %b %H:%M'), backends=out), open(os.path.join(HERE, 'summary.json'), 'w'), indent=1)
    try:
        import subprocess; subprocess.run([sys.executable, os.path.join(HERE, 'publish_qia_ibm.py')], timeout=120)
    except Exception as e: print('publish step failed', type(e).__name__)
    print('mirror:', len(names), 'processors,', sum(1 for n in names if state.get(n, {}).get('last_read') == now), 'read')
if __name__ == '__main__': main()
