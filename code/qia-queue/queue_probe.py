"""queue_probe.py (--open: on IBM's Open plan, the free shared line, 600 s per 28 days): the smallest real job on each IBM processor (one qubit, X, measure, one shot), to time how long a job waits from
submission to running. One probe outstanding per processor at most: a processor with a probe still waiting is skipped. Every probe is
tagged qia-queue-probe and logged in data/probes.jsonl; finished probes get their wait and their charged seconds written back.
Budget guards: never below KEEP_S account seconds, never more than DAY_CAP_S charged to probes in the last 24 hours.
Run: python3 -I queue_probe.py            (one round: collect finished probes, then one probe to the processor read longest ago)
     python3 -I queue_probe.py --all      (a probe to every processor without one waiting)
     python3 -I queue_probe.py --one ibm_fez   (a single probe, for measuring the cost)"""
import os, sys, json, time, datetime as dt
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.expanduser('~/bones-forge'); LOG = H + '/data/probes.jsonl'
PLAN = 'open' if '--open' in sys.argv else ('eu' if '--eu' in sys.argv else 'paid'); OPEN = PLAN == 'open'
TAG = {'paid': 'qia-queue-probe', 'eu': 'qia-queue-probe-eu', 'open': 'qia-queue-probe-open'}[PLAN]
# 30 Oct (his "why are you limiting us to the open plan ... we have every us east and europe plan"): every processor every hour on the paid plans; one probe is charged 2 s
KEEP_S, DAY_CAP_S = {'paid': (100, 10 ** 9), 'eu': (50, 10 ** 9), 'open': (200, 20)}[PLAN]
LOG = H + {'paid': '/data/probes.jsonl', 'eu': '/data/probes_eu.jsonl', 'open': '/data/probes_open.jsonl'}[PLAN]
def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    if PLAN in ('open', 'eu'):   # his Parallax key: the Open plan line (us-east) or the Quaker instance (eu-de, ibm_aachen)
        tok = open(B + '/.ibm_quantum_key_parallax').read().strip(); want = 'open' if PLAN == 'open' else 'eu-de'
        s0 = QiskitRuntimeService(channel='ibm_quantum_platform', token=tok)
        crn = [i['crn'] for i in s0.instances() if isinstance(i, dict) and ((i.get('plan') == 'open') if PLAN == 'open' else (':eu-de:' in i['crn']))][0]
        return QiskitRuntimeService(channel='ibm_quantum_platform', token=tok, instance=crn)
    tok = open(B + '/.ibm_quantum_key_3').read().strip(); crn = open(B + '/.ibm_quantum_instance_crn').read().strip()
    return QiskitRuntimeService(channel='ibm_cloud', token=tok, instance=crn)
def rows():
    return [json.loads(l) for l in open(LOG)] if os.path.exists(LOG) else []
def collect(s):
    out, changed = rows(), False
    for r in out:
        if r.get('state') in ('DONE', 'ERROR', 'CANCELLED'): continue
        j = s.job(r['id']); st = str(j.status()); m = j.metrics(); ts = m.get('timestamps') or {}
        if ts.get('running') and not r.get('wait_s'):
            c = dt.datetime.fromisoformat(str(ts['created']).replace('Z', '+00:00')); u = dt.datetime.fromisoformat(str(ts['running']).replace('Z', '+00:00'))
            r['wait_s'] = round((u - c).total_seconds(), 1); changed = True
        if st in ('DONE', 'ERROR', 'CANCELLED'):
            r['state'] = st; r['charged_s'] = (m.get('usage') or {}).get('qpu_charge_time_seconds'); changed = True
    if changed:
        with open(LOG, 'w') as f:
            for r in out: f.write(json.dumps(r) + '\n')
    return out
def send(s, be):
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import SamplerV2
    qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0); isa = transpile(qc, be, optimization_level=1)
    sm = SamplerV2(mode=be); sm.options.environment.job_tags = [TAG]
    front = be.status().pending_jobs
    j = sm.run([isa], shots=1); r = dict(id=j.job_id(), backend=be.name, sent=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), state='SENT', front_at_send=front)
    with open(LOG, 'a') as f: f.write(json.dumps(r) + '\n')
    print('probe sent', be.name, j.job_id(), flush=True)
if __name__ == '__main__':
    os.makedirs(H + '/data', exist_ok=True); s = service(); out = collect(s)
    if '--collect' in sys.argv: print('probe: collected', PLAN, sum(1 for r in out if r.get('wait_s') is not None), 'with waits'); sys.exit(0)   # status reads only, no job sent
    day = time.time() - 86400; spent = sum(r.get('charged_s') or 0 for r in out if dt.datetime.fromisoformat(r['sent'].replace('Z', '+00:00')).timestamp() > day)
    rem = s.usage().get('usage_remaining_seconds')
    if rem is not None and rem < KEEP_S: print('probe: held, account at %s s (keep %s)' % (rem, KEEP_S)); sys.exit(0)
    if spent >= DAY_CAP_S: print('probe: held, %s s charged to probes in 24 h (cap %s)' % (spent, DAY_CAP_S)); sys.exit(0)
    waiting = {r['backend'] for r in out if r.get('state') == 'SENT' and not r.get('wait_s')}
    if '--one' in sys.argv: names = [sys.argv[sys.argv.index('--one') + 1]]
    elif '--all' in sys.argv or PLAN in ('paid', 'eu'): names = sorted(b.name for b in s.backends(operational=True, simulator=False))
    else:   # default, one round per hour of her ticks: the operational processor whose last probe is oldest (never probed first), one probe
        ops = sorted(b.name for b in s.backends(operational=True, simulator=False)); last = {}
        for r in out: last[r['backend']] = max(last.get(r['backend'], ''), r['sent'])
        cand = [n for n in ops if n not in waiting]; names = sorted(cand, key=lambda n: last.get(n, ''))[:1]
    for n in names:
        if n in waiting: print('probe: %s still waiting, skipped' % n); continue
        send(s, s.backend(n))
    print('probe: round done; %s s charged to probes in 24 h; account %s s' % (spent, rem))
