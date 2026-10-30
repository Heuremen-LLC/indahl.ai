#!/usr/bin/env python3
"""cal.py: the hourly calibration (PLAN.md). One job per processor: C0 (all qubits at rest, measured), C1 (X on all, measured), and X then a delay
at 15, 40, 80, 160, 320 us, measured, all qubits at once. IBM's record is saved right before the job. Each finished job is read against that record
(callib.analyse), published (KV qia_cal and qia_cal_<job>), and added to the off-record chain (qia_offchain/entries.jsonl -> KV qia_offchain).
The job's wait (created -> running) is written to the queue log as a by-product.
Run: --send [--eu]      one job per processor without a job still waiting (budget floor KEEP_S)
     --collect [--eu]   read finished jobs, analyse, publish, chain (status reads only)
"""
import os, sys, json, time, hashlib, subprocess, datetime as dt
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H); sys.path.insert(0, H)
import callib as C
EU = '--eu' in sys.argv; KEEP_S = 50 if EU else 100
RUNS = H + ('/data/runs_eu.jsonl' if EU else '/data/runs.jsonl'); QLOG = B + ('/qia_queue/data/probes_eu.jsonl' if EU else '/qia_queue/data/probes.jsonl')
TAG = 'qia-calibration-eu' if EU else 'qia-calibration'; SRO, ST1 = 1000, 500
W = B + '/cloudflare-workers/heuremen-door'; NS = 'ecb59d96b07c43bdac14271687eae5af'
def service():
    """Your own IBM account: IBM_QUANTUM_TOKEN, and IBM_QUANTUM_INSTANCE (the CRN) if you have more than one instance."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    inst = os.environ.get('IBM_QUANTUM_INSTANCE')
    return QiskitRuntimeService(channel='ibm_quantum_platform', token=os.environ['IBM_QUANTUM_TOKEN'], **({'instance': inst} if inst else {}))
def rows(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
def kv(key, path):
    env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID='f069aa0c8534706cb64f7cc3658dd894', PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')
    return subprocess.run(['/opt/homebrew/bin/npx', 'wrangler', 'kv', 'key', 'put', key, '--path', path, '--namespace-id', NS, '--remote'], cwd=W, env=env, capture_output=True, text=True).returncode == 0
def usable(be):
    t = be.target; return [q for q in range(be.num_qubits) if t.instruction_supported('x', (q,)) and t.instruction_supported('measure', (q,))]
def circuits(be, qs):
    from qiskit import QuantumCircuit, transpile
    dt_s = be.target.dt; out = []
    def base(x, d_us):
        qc = QuantumCircuit(be.num_qubits, len(qs))
        if x:
            for q in qs: qc.x(q)
        if d_us:
            n = int(round(d_us * 1e-6 / dt_s / 16)) * 16
            for q in qs: qc.delay(n, q, unit='dt')
        qc.barrier()
        for i, q in enumerate(qs): qc.measure(q, i)
        return qc
    raw = [base(False, 0), base(True, 0)] + [base(True, d) for d in C.DELAYS_US[1:]]
    return [transpile(c, be, optimization_level=0, initial_layout=list(range(be.num_qubits)), layout_method='trivial') for c in raw]
def send(s, be):
    from qiskit_ibm_runtime import SamplerV2
    qs = usable(be); props = be.properties(refresh=True).to_dict()
    pubs = [(c, None, SRO if i < 2 else ST1) for i, c in enumerate(circuits(be, qs))]
    sm = SamplerV2(mode=be); sm.options.environment.job_tags = [TAG]; front = be.status().pending_jobs
    j = sm.run(pubs); jid = j.job_id(); now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json.dump(dict(qubits=qs, props=props), open(H + '/data/rec_%s.json' % jid, 'w'), default=str)
    with open(RUNS, 'a') as f: f.write(json.dumps(dict(id=jid, backend=be.name, sent=now, state='SENT', qubits=len(qs), front_at_send=front)) + '\n')
    with open(QLOG, 'a') as f: f.write(json.dumps(dict(id=jid, backend=be.name, sent=now, state='SENT', front_at_send=front, kind='calibration')) + '\n')
    print('cal sent', be.name, jid, len(qs), 'qubits', flush=True)
def stated_of(props, qs):
    by = {}
    for i, ql in enumerate(props['qubits']):
        d = {p['name']: (p['value'], str(p.get('date', ''))[:16]) for p in ql}; by[i] = d
    out, dates = {}, {}
    for k, q in enumerate(qs):
        d = by.get(q, {}); g = lambda n: d.get(n, (None, ''))[0]
        out[k] = dict(p10=g('prob_meas1_prep0'), p01=g('prob_meas0_prep1'), t1=g('T1')); dates[k] = dict(p10=d.get('prob_meas1_prep0', (0, ''))[1], p01=d.get('prob_meas0_prep1', (0, ''))[1], t1=d.get('T1', (0, ''))[1])
    return out, dates
def read(job, qs):
    import numpy as np
    res = job.result(); cnt = []
    for pub in res:
        reg = getattr(pub.data, 'c', None) or getattr(pub.data, 'meas'); bits = reg.get_bitstrings()
        a = np.array([[ch == '1' for ch in b[::-1]] for b in bits], bool)   # column k = clbit k = qubit qs[k]
        cnt.append(a.sum(0))
    c0 = cnt[0]; c1z = SRO - cnt[1]; t1 = np.column_stack(cnt[2:])
    return c0, c1z, t1
def chain_append(entry):
    E = B + '/qia_offchain/entries.jsonl'
    with open(E, 'a') as f: f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    sys.path.insert(0, B + '/qia_offchain'); import chain as CH
    c = CH.build(); CH.verify(B + '/qia_offchain/chain.json'); kv('qia_offchain', B + '/qia_offchain/chain.json'); return c['head']
def process(s, r, corrects=None):
    """Read one finished job against the record in force when it ran; publish; add a chain entry. corrects = chain entry number it corrects."""
    j = s.job(r['id']); rec = json.load(open(H + '/data/rec_%s.json' % r['id'])); qs = rec['qubits']
    m = j.metrics(); ts = m.get('timestamps') or {}; win = [str(ts.get('running', ''))[:19] + 'Z', str(ts.get('finished', ''))[:19] + 'Z']
    # /q 3: the record in force when the job RAN (a job can wait hours; IBM refreshes its record meanwhile)
    run_props = s.backend(r['backend']).properties(datetime=dt.datetime.fromisoformat(win[0].replace('Z', '+00:00'))).to_dict()
    json.dump(run_props, open(H + '/data/rec_run_%s.json' % r['id'], 'w'), default=str)
    stated, dates = stated_of(run_props, qs)
    c0, c1z, t1 = read(j, qs); rows_, kg = C.analyse(c0, c1z, t1, SRO, ST1, stated)
    per = []
    for k, q in enumerate(qs):
        x = dict(qubit=q, **rows_[k]); x.update(ibm_p10_date=dates[k]['p10'], ibm_p01_date=dates[k]['p01'], ibm_t1_date=dates[k]['t1']); per.append(x)
    full = dict(processor=r['backend'], job_id=r['id'], window_utc=win, record_used='IBM record in force at the job start (%s)' % win[0], record_saved_at_send=r['sent'],
                rule='qia_cal PLAN.md with Note 1', shots=dict(readout=SRO, t1=ST1), delays_us=C.DELAYS_US, **kg, qubits=per,
                raw=dict(c0_ones=[int(v) for v in c0], c1_zeros=[int(v) for v in c1z], t1_ones=[[int(v) for v in row] for row in t1]))
    fp = H + '/data/res_%s.json' % r['id']; json.dump(full, open(fp, 'w')); sha = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
    kv('qia_cal_' + r['id'], fp)
    off = []
    for x in per:
        for qn, lab, un in (('p10', 'readout P(1|0)', ''), ('p01', 'readout P(0|1)', ''), ('t1', 'T1', 'us')):
            if x[qn + '_outcome'] in ('ABOVE', 'BELOW'):
                off.append(dict(qubit=x['qubit'], quantity=lab, ibm=x['ibm_' + qn], ibm_date=x['ibm_%s_date' % qn], measured=x[qn], interval=x[qn + '_ci'], unit=un, outcome=x[qn + '_outcome']))
    counts = {qn: {o: sum(1 for x in per if x[qn + '_outcome'] == o) for o in ('ABOVE', 'BELOW', 'CONSISTENT', 'CANNOT_TELL')} for qn in ('p10', 'p01', 't1')}
    e = dict(type='calibration run', added=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), processor=r['backend'], qubits_read=len(qs), window_utc=win, job_id=r['id'],
             rule='qia_cal PLAN.md with Note 1 (readout: IBM count vs ours, both exact 99.9%, call on non-overlap; T1: 99.99% interval, 25% margin)',
             known_good=kg['known_good'], counts=counts, off=off, results='/qia/cal/%s.json' % r['id'], results_sha256=sha)
    if corrects: e['corrects'] = corrects
    head = chain_append(e)
    print('cal read', r['backend'], r['id'], kg['known_good'], 'off', len(off), 'chain head', head[:12], flush=True)
    return dict(job_id=r['id'], window_utc=win, qubits_read=len(qs), known_good=kg['known_good'], counts=counts, off=len(off),
                median_readout_measured_over_stated=kg['median_readout_measured_over_stated'], median_t1_measured_over_stated=kg['median_t1_measured_over_stated']), m
def publish_latest(latest):
    latest_p = H + '/data/latest.json'; old = json.load(open(latest_p)) if os.path.exists(latest_p) else {}; old.update(latest); json.dump(old, open(latest_p, 'w'), indent=1)
    pub = H + '/data/qia_cal.json'; json.dump(dict(updated=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), processors=old), open(pub, 'w'), indent=1); kv('qia_cal', pub)
def collect(s):
    rs = rows(RUNS); changed = False; latest = {}
    for r in rs:
        if r.get('state') != 'SENT': continue
        st = str(s.job(r['id']).status())
        if st in ('ERROR', 'CANCELLED'): r['state'] = st; changed = True; continue
        if st != 'DONE': continue
        summ, m = process(s, r); latest[r['backend']] = summ
        r['state'] = 'DONE'; r['charged_s'] = (m.get('usage') or {}).get('qpu_charge_time_seconds'); changed = True
    if changed:
        with open(RUNS, 'w') as f:
            for r in rs: f.write(json.dumps(r) + '\n')
    if latest: publish_latest(latest)
    return rs
if __name__ == '__main__' and '--reread' in sys.argv:   # Note 1 correction: re-read a finished job, chain entry names the entry it corrects
    s = service(); jid = sys.argv[sys.argv.index('--reread') + 1]; n = int(sys.argv[sys.argv.index('--corrects') + 1])
    r = [x for x in rows(RUNS) if x['id'] == jid][0]; summ, m = process(s, r, corrects=n); publish_latest({r['backend']: summ}); sys.exit(0)
if __name__ == '__main__':
    os.makedirs(H + '/data', exist_ok=True); s = service(); rs = collect(s)
    if '--collect' in sys.argv: sys.exit(0)
    rem = s.usage().get('usage_remaining_seconds')
    if rem is not None and rem < KEEP_S: print('cal: held, account at %s s (keep %s)' % (rem, KEEP_S)); sys.exit(0)
    waiting = {r['backend'] for r in rs if r.get('state') == 'SENT'}
    names = [sys.argv[sys.argv.index('--one') + 1]] if '--one' in sys.argv else sorted(b.name for b in s.backends(operational=True, simulator=False))
    for n in names:
        if n in waiting: print('cal: %s still waiting, skipped' % n); continue
        try: send(s, s.backend(n))
        except Exception as e: print('cal: send failed', n, type(e).__name__, str(e)[:160])
    print('cal: round done; account %s s' % rem)
